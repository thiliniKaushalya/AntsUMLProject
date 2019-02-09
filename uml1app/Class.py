import nltk
import re
from nltk.tokenize import sent_tokenize, word_tokenize
import sqlite3
from .models import ClassNames
from .models import ClassAttributes
from .models import ClassMethods
from .models import ClassLoop
from .models import ClassRelationships
from .models import NotIdentifiedClasses
from .models import CompositionRelationship
from .models import IdentifiedAggrigations
import inflect
p=inflect.engine()


class Class:
    def classpre_processing(sentence_pre):  # method for Actor button
        sentence_pre = sentence_pre.replace("•", " ")
        tokens = nltk.word_tokenize(sentence_pre)
        simpletokens = [x.lower() for x in tokens]
        tagged = nltk.pos_tag(simpletokens)
        t = []
        temp = ""
        for indi,tag in enumerate(tagged):
            if tagged[indi - 1][1] == 'NN' and tagged[indi][1] == 'NNS':
                temp = nltk.pos_tag(
                    nltk.word_tokenize(p.plural(tagged[indi - 1][0]) + " " + p.singular_noun(tagged[indi][0])))
                if temp[1][1] == 'VBP':
                    t.append((temp[1][0], temp[1][1]))
                temp = ""
            else:
                t.append(tuple(tag))
        tagged = t
        for wordtuple in tagged:
            print(wordtuple)

        return tagged

    def filtering_classess(sentence_for_classes):
        classes = []
        print(classes)
        print("classes")

        taggedsent = Class.classpre_processing(sentence_for_classes)
        ClassRelationships.objects.all().delete()
        NotIdentifiedClasses.objects.all().delete()
        IdentifiedAggrigations.objects.all().delete()
        CompositionRelationship.objects.all().delete()

        num = 1

        for ind, word in enumerate(taggedsent):
            if (taggedsent[ind - 6][1] == 'NN' or taggedsent[ind - 6][1] == 'NNP') and taggedsent[ind - 5][1] == 'VBZ' and taggedsent[ind - 4][1] == 'DT' and taggedsent[ind - 3][0] == 'part' and taggedsent[ind - 2][0] == 'of' and taggedsent[ind-1][1] == 'DT' and (taggedsent[ind][1] == 'NN' or taggedsent[ind][1] == 'NNP') and len(taggedsent) > 6:
                    classes.append(taggedsent[ind - 6][0])  # Aggregation is identified
                    classes.append(taggedsent[ind][0])
                    if num == 1:
                        classaggregation = IdentifiedAggrigations(names=taggedsent[ind][0] + " o-left- " + taggedsent[ind - 6][0])
                        classaggregation.save()
                        num = 2
                    elif num == 2:
                        classaggregation = IdentifiedAggrigations(names=taggedsent[ind-6][0] + " o-right- " + taggedsent[ind][0])
                        classaggregation.save()
                        num = 3
                    elif num == 3:
                        classaggregation = IdentifiedAggrigations(names=taggedsent[ind-6][0] + " o-up- " + taggedsent[ind][0])
                        classaggregation.save()
                        num = 4
                    elif num == 4:
                        classaggregation = IdentifiedAggrigations(names=taggedsent[ind-6][0] + " o-down- " + taggedsent[ind][0])
                        classaggregation.save()
                        num = 1
                    cr = CompositionRelationship(names=taggedsent[ind][0], nextclass=taggedsent[ind - 6][0])
                    print(cr.names)
                    cr.save()
            elif (taggedsent[ind-3][1] == 'NN' or taggedsent[ind-3][1] == 'NNP') and taggedsent[ind-2][0] == 'is' and (taggedsent[ind-1][0] == 'a' or taggedsent[ind-1][0] == 'an') and taggedsent[ind][1] == 'NN' and taggedsent[ind][0] != 'part':
                classes.append(taggedsent[ind-3][0])#inheritance is identified
                classes.append(taggedsent[ind][0])
                classinheritance = ClassRelationships(names=taggedsent[ind][0]+"<|--"+taggedsent[ind-3][0])
                classinheritance.save()
            # elif taggedsent[ind-2][1] == 'NN' and taggedsent[ind-1][1] == 'VBZ' and taggedsent[ind][1] == 'VBN':
            #     classes.append(taggedsent[ind-2][0])
                # Class.NotIdentifiedClassesMethod(taggedsent[ind-2][0])
            elif taggedsent[ind-3][1] == 'DT' and taggedsent[ind-2][1] == 'JJ' and taggedsent[ind-1][1] == 'NN' and taggedsent[ind][1] == '.':
                classes.append(taggedsent[ind-1][0])
                # Class.NotIdentifiedClassesMethod(word[0])
            elif (taggedsent[ind-1][1] == 'NN' or taggedsent[ind-1][1] == 'NNS') and taggedsent[ind][1] == 'VBP':
                classes.append(taggedsent[ind-1][0])
                # Class.NotIdentifiedClassesMethod(taggedsent[ind-1][0])
            elif taggedsent[ind-1][1] == 'NN' and (taggedsent[ind][1] == 'VBZ' and taggedsent[ind][0] != 'is'):# e.g:has 'VBZ'
                classes.append(taggedsent[ind-1][0])
                # Class.NotIdentifiedClassesMethod(taggedsent[ind-1][0])
            elif taggedsent[ind-2][0] == 'the' and taggedsent[ind-1][1] == 'NN' and taggedsent[ind][1] == '.':
                classes.append(taggedsent[ind-1][0])

        ClassNames.objects.all().delete()

        templist = list()#for database saving-so removeduplicates and make all classes singular
        returnlist = list()# Not only singular.but remove duplicates.
        for cl in classes:
            if cl not in returnlist:
                returnlist.append(cl)
            info = ""
            if str(p.singular_noun(cl)) == "False":
                if cl not in templist:
                    templist.append(cl)
            else:
                info = p.singular_noun(cl)
                if info not in templist:
                    templist.append(info)

        for t in templist:
            classinfo = ClassNames(names=t)
            classinfo.save()

        return list(returnlist)

    def class_features(sentence_for_classes):
        classarr = {}
        taggedsent2 = Class.classpre_processing(sentence_for_classes+" . . . .")
        obclasses = Class.filtering_classess(sentence_for_classes)
        singularclasses = []
        pluralclasses = []
        for cla in obclasses:
            if str(p.singular_noun(cla)) == "False":
                singularclasses.append(cla)
                pluralclasses.append(p.plural(cla))
            else:
                singularclasses.append(p.singular_noun(cla))
                pluralclasses.append(cla)
        for ob in obclasses:
                    attr = []
                    for ind, word in enumerate(taggedsent2):
                        if taggedsent2[ind - 2][0] == ob and (taggedsent2[ind - 1][1] == 'VBZ' and taggedsent2[ind - 1][0] != 'has') and (taggedsent2[ind][1] == 'VBN' or taggedsent2[ind][0] == 'been'):
                            attr.append("V" + taggedsent2[ind][0])
                        elif taggedsent2[ind - 2][1] == 'DT' and taggedsent2[ind - 1][1] == 'JJ' and taggedsent2[ind][0] == ob:
                            attr.append("J" + taggedsent2[ind - 1][0])
                        elif taggedsent2[ind - 1][0] == ob and taggedsent2[ind][1] == 'VBP':
                            attr.append("V" + taggedsent2[ind][0])
                        elif taggedsent2[ind - 2][0] == ob and (taggedsent2[ind-1][1] == 'VBZ' and taggedsent2[ind-1][0] != 'is' and taggedsent2[ind-1][0] != 'has' and taggedsent2[ind-1][0] != 'contains') and taggedsent2[ind][1] == 'DT':
                            attr.append("V" + taggedsent2[ind-1][0])
                        elif taggedsent2[ind-1][0] == ob and ((taggedsent2[ind][1] == 'VBZ' and taggedsent2[ind][0] != 'is') or taggedsent2[ind][1] == 'MD') :#e.g.has,contains 'VBZ'
                            tempind = ind + 1
                            while len(taggedsent2) > tempind:
                                if (not (taggedsent2[tempind][0] not in obclasses)) or taggedsent2[tempind][0] == '.':
                                    break
                                elif taggedsent2[tempind][1] == 'NN' or (taggedsent2[tempind][1] == 'NNS' and taggedsent2[tempind][0] != 'types' and (taggedsent2[tempind][0] not in pluralclasses)):
                                    attr.append("J" + taggedsent2[tempind][0])
                                elif taggedsent2[tempind][1] == 'VBG' or (taggedsent2[tempind][1] == 'VBN' and taggedsent2[tempind][0] != 'been') or (taggedsent2[tempind][1] == 'VB' and taggedsent2[tempind][0] != 'be'and taggedsent2[tempind][0] != 'have') or taggedsent2[tempind][1] == 'VBD':
                                    attr.append("V" + taggedsent2[tempind][0])
                                tempind = tempind + 1

                        # Class Mapping
                        if (taggedsent2[ind-1][1] == 'DT' or taggedsent2[ind-2][1] == '.' or (ind == 0)) and taggedsent2[ind][0] == ob:
                            tempind = ind + 1
                            while len(taggedsent2) > tempind+3:
                                multiclassTF = False
                                multiclass = ""
                                if (not (p.singular_noun(taggedsent2[tempind + 2][0]) not in obclasses)):
                                    multiclassTF = True
                                    multiclass = p.singular_noun(taggedsent2[tempind + 2][0])
                                elif (not (taggedsent2[tempind+2][0] not in obclasses)):
                                    multiclassTF = True
                                    multiclass = taggedsent2[tempind+2][0]

                                multiclassTF2 = False
                                multiclass2 = ""
                                if (not (p.singular_noun(taggedsent2[tempind + 3][0]) not in obclasses)):
                                    multiclassTF2 = True
                                    multiclass2 = p.singular_noun(taggedsent2[tempind + 3][0])
                                elif (not (taggedsent2[tempind + 3][0] not in obclasses)):
                                    multiclassTF2 = True
                                    multiclass2 = taggedsent2[tempind + 3][0]

                                multiclassTF3 = False
                                multiclass3 = ""
                                if (not (p.singular_noun(taggedsent2[tempind + 4][0]) not in obclasses)):
                                    multiclassTF3 = True
                                    multiclass3 = p.singular_noun(taggedsent2[tempind + 4][0])
                                elif (not (taggedsent2[tempind + 4][0] not in obclasses)):
                                    multiclassTF3 = True
                                    multiclass3 = taggedsent2[tempind + 4][0]

                                print(str(taggedsent2[tempind][1] == 'VBP')+taggedsent2[tempind][0]+(taggedsent2[tempind + 3][0]))

                                if (not (taggedsent2[tempind][0] not in obclasses)) or taggedsent2[tempind][1] == '.':
                                    break
                                elif (taggedsent2[tempind][1] == 'VB'or taggedsent2[tempind][1] == 'VBN') and taggedsent2[tempind+1][0] == 'multiple' and multiclassTF:
                                    classmapping = ClassRelationships(names=ob + "\"1\" -- \"many\" " + multiclass+" : "+taggedsent2[tempind][0])
                                    classmapping.save()
                                elif (taggedsent2[tempind][1] == 'VBZ') and taggedsent2[tempind+1][0] == 'any' and multiclassTF3:
                                    classmapping = ClassRelationships(names=ob + "\"1\" -- \"many\" " + multiclass3+" : "+taggedsent2[tempind][0])
                                    classmapping.save()
                                elif (taggedsent2[tempind][1] == 'VB' or taggedsent2[tempind][1] == 'VBN') and taggedsent2[tempind+1][0] == 'a' and multiclassTF:
                                    classmapping = ClassRelationships(names=ob + "\"1\" -- \"1\" " + multiclass+" : "+taggedsent2[tempind][0])
                                    classmapping.save()
                                elif (taggedsent2[tempind][1] == 'VB' or taggedsent2[tempind][1] == 'VBN') and taggedsent2[tempind+1][0] == 'a' and taggedsent2[tempind+2][1] == 'JJ' and multiclassTF:
                                    classmapping = ClassRelationships(names=ob + "\"1\" -- \"1\" " + multiclass2+" : "+taggedsent2[tempind][0])
                                    classmapping.save()
                                elif (taggedsent2[tempind][1] == 'VBP' or taggedsent2[tempind][1] == 'VBN') and multiclassTF3:
                                    classmapping = ClassRelationships(names=ob + "\"1\" -- \"1\" " + multiclass3 +" : "+taggedsent2[tempind][0])
                                    classmapping.save()
                                elif (taggedsent2[tempind][1] == 'VBP' or taggedsent2[tempind][1] == 'VBN') and multiclassTF2:
                                    classmapping = ClassRelationships(names=ob + "\"1\" -- \"1\" " + multiclass2 +" : "+taggedsent2[tempind][0])
                                    classmapping.save()

                                tempind = tempind + 1

                        # types of
                        nxtcl = ""
                        todb = ""
                        if taggedsent2[ind][0] == ob:
                            nxtcl = ob
                            todb = nxtcl
                        else:
                            if str(p.singular_noun(ob)) == "False":
                                todb = ob
                                nxtcl = p.plural(ob)
                            else:
                                nxtcl = p.singular_noun(ob)
                                todb = nxtcl

                        if taggedsent2[ind-2][0] == 'types' and taggedsent2[ind-1][0] == 'of' and taggedsent2[ind][0] == nxtcl:
                            tempind = ind + 1
                            while len(taggedsent2) > tempind:
                                if taggedsent2[tempind][0] == '.':
                                    break
                                elif taggedsent2[tempind][1] == 'JJ' and taggedsent2[tempind + 1][0] == nxtcl:
                                    inheritance = ClassRelationships(names=todb+"<|--"+taggedsent2[tempind][0]+"_"+todb)
                                    inheritance.save()
                                tempind = tempind + 1

                    if str(p.singular_noun(ob)) == "False":
                        if ob not in classarr:
                            classarr[ob] = attr
                        else:
                            if attr != []:
                                classarr[ob].append(attr[0])
                    else:
                        if p.singular_noun(ob) not in classarr:
                            classarr[p.singular_noun(ob)] = attr
                        else:
                            if attr != []:
                                classarr[p.singular_noun(ob)].append(attr[0])

        for key, values in classarr.items():
            print(key)
            print(values)

        return classarr.items()

    def filtering_attributes(sentattr):
        attrlist = {}
        fattr = []
        classsent = Class.class_features(sentattr)
        for k, v in classsent:
            if v is not None:
                for i in v:
                    if i.startswith('J'):
                        s = list(i)
                        s[0] = ""
                        s ="".join(s)
                        if s not in fattr:
                            fattr.append(s)
            attrlist[k] = fattr
            fattr = []

        print("attributes")
        ClassAttributes.objects.all().delete()
        for key, values in attrlist.items():
            classattributes = ClassAttributes(names=key, attributes=', '.join(attrlist.get(key)))
            classattributes.save()

        return attrlist.items()

    def filtering_methods(sentmethods):
        attrlist = {}
        fmethods = []
        classsent = Class.class_features(sentmethods)
        for k, v in classsent:
            if v is not None:
                for i in v:
                    if i.startswith('V'):
                        s = list(i)
                        s[0] = ""
                        s="".join(s)
                        if s not in fmethods:
                            fmethods.append(s)
            attrlist[k] = fmethods
            fmethods = []

        print("methods")
        ClassMethods.objects.all().delete()
        for key, values in attrlist.items():
            classmethods = ClassMethods(names=key, methods=', '.join(attrlist.get(key)))
            classmethods.save()

        return attrlist.items()

    def loopingclasses(classlist):
        classset = {}
        i = 0
        flag = 0
        taggy = 0

        while i < len(classlist)-1:
            if flag == 0:
                classset[classlist[i].names] = classlist[len(classlist)-1].names
                flag = 1
            classset[classlist[i].names] = classlist[i+1].names
            i = i + 1

        ClassLoop.objects.all().delete()
        for key, values in classset.items():
            classloops = ClassLoop(names=key, anotherclass=values)
            classloops.save()

        return classset.items()

    def NotIdentifiedClassesMethod(word):
        NotIdentifiedClassesarr = []
        for i in NotIdentifiedClasses.objects.all():
            NotIdentifiedClassesarr.append(i.names)

        if str(p.singular_noun(word)) == "False":
            if word not in NotIdentifiedClassesarr:
                NotIdentifiedClassesarr.append(word)
                ni = NotIdentifiedClasses(names=word)
                ni.save()
        else:
            if p.singular_noun(word) not in NotIdentifiedClassesarr:
                NotIdentifiedClassesarr.append(p.singular_noun(word))
                ni = NotIdentifiedClasses(names=p.singular_noun(word))
                ni.save()

        print(NotIdentifiedClassesarr)
        print("NotIdentifiedClassesarr")










